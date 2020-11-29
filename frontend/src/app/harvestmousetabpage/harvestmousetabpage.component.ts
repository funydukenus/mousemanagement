import { Component, OnInit, AfterViewInit, ViewChildren, ViewChild, QueryList, ChangeDetectorRef } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DataproviderService } from '../service/dataprovider.service';
import { ToastmessageService, SuccessColor, ErrorColor } from '../service/toastmessage.service';
import { HarvestmousepageComponent } from '../harvestmousepage/harvestmousepage.component';
import { HarvestMouse } from '../interface/harvestmouse';
import { MatTableDataSource } from '@angular/material/table';
import { BottomsheetService } from '../service/bottomsheet.service';
import { MatBottomSheet } from '@angular/material/bottom-sheet';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { DiagService } from '../service/diag.service';
import { MatDialog } from '@angular/material/dialog';
import { EventEmiterService } from '../service/event.emmiter.service';
import { MatDrawer } from '@angular/material/sidenav';

interface TabConfig {
   filterString: string[],
   tabName: string,
   datasource: MatTableDataSource<HarvestMouse>,
   harvestMouseList: HarvestMouse[],
   tabComponent: HarvestmousepageComponent
}

@Component({
   selector: 'app-harvestmousetabpage',
   templateUrl: './harvestmousetabpage.component.html',
   styleUrls: ['./harvestmousetabpage.component.scss']
})
export class HarvestmousetabpageComponent implements OnInit, AfterViewInit {
   // Qeury set for all the HarvestmousepageComponent directives
   // with tab id
   @ViewChildren('tab') tabList: QueryList<HarvestmousepageComponent>;

   loaded: boolean;
   trackedLoadedTabCom: number = 0;

   tabConfig: TabConfig[] = [];

   activeTabConfig: TabConfig;

   groupSelectedEnabled: boolean;

   // selected harvested mouse
   selectedHarvestedMouse: HarvestMouse[];

   loading_twice_or_more: boolean;

   @ViewChild('sidenav') sideNav: MatDrawer;

   constructor(
      private dataprovider: DataproviderService,
      private toastservice: ToastmessageService,
      private diagservice: DiagService,
      private _snackBar: MatSnackBar,
      private bottomsheetservice: BottomsheetService,
      private bottomSheet: MatBottomSheet,
      private diaglog: MatDialog,
      private cdr: ChangeDetectorRef,
      private _eventEmiter: EventEmiterService
   ) {
      this.showInProgress();
      this._eventEmiter.informPageLoc(
         'mousetable'
      );
   }

   refreshTabAndData(): void {
      let project_list: string[];
      this.loading_twice_or_more = true;
      this.dataprovider.getDataList().subscribe(
         data => {
            project_list = data['projectTitleList'];
            project_list.forEach(
               tab_cri => {
                  let filterInputString = "project_title@" + tab_cri + "@4";
                  let existed: boolean = false;
                  let not_existed: boolean = true;
                  // Checks if exists
                  this.tabConfig.forEach(
                     data => {
                        if (data.tabName == tab_cri) {
                           existed = true;
                           return;
                        }
                     }
                  )

                  // Checks if exists
                  this.tabConfig.forEach(
                     data => {
                        if (!(project_list.includes(data.tabName))) {
                           this.removeFromTab(data);
                           not_existed = true;
                           return;
                        }
                     }
                  )

                  if (not_existed && existed) {
                     return;
                  }

                  this.tabConfig.push(
                     {
                        tabName: tab_cri,
                        filterString: [filterInputString],
                        datasource: new MatTableDataSource<HarvestMouse>(),
                        harvestMouseList: [],
                        tabComponent: null
                     }
                  );
               }
            )

            this.cdr.detectChanges();

            // Convert view children query set to array
            this.tabList.toArray().forEach(
               // For each of found HarvestedMouse Component
               curTabCom => {
                  // For each of the tab config
                  this.tabConfig.forEach(
                     tabConfigEle => {
                        let tabNameFromTabConfig: string = tabConfigEle.tabName;

                        // If the found HarvestedMouse has the same tabName
                        // as the tabConfig, assign the tabComponent
                        // to this tabConfig
                        if (tabNameFromTabConfig == curTabCom.tabName) {
                           tabConfigEle.tabComponent = curTabCom;
                        }
                     }
                  )
               }
            )

            // Fresh All the mouse lists in each of the tabs
            this.refreshMouseListsAllTabs();
         }
      );
   }

   removeFromTab(value) {
      const index = this.tabConfig.indexOf(value);
      if (index > -1) {
         this.tabConfig.splice(index, 1);
      }

   }

   ngOnInit(): void {
      this.refreshTabAndData();

   }

   /*
   Funtion name: ngAfterViewInit
   Description: Based on the document,Respond after Angular checks the component's
                views and child views / the view that a directive is in.
                Called after the ngAfterViewInit() and every subsequent
                ngAfterContentChecked().
   */
   ngAfterViewInit(): void {
      // Placeholder for other actions if needed
   }

   /*
   Function name: refreshMouseListsAllTabs
   Description: This is the method refresh all the tabs with existing
                datasource assign to the tabConfig
   */
   refreshMouseListsAllTabs() {
      console.log(this.tabConfig);
      this.tabConfig.forEach(
         tabConfig => {
            this.GetMouseTabList(
               tabConfig
            );
         }
      );

      this.activeTabConfig = this.tabConfig[0];
   }

   /*
   Function name: GetMouseList
   Description: This function trigger get method to get the mouse list
                and populate to the table
   */
   GetMouseTabList(tabConfig: TabConfig) {
      // Load the harvested mouse list when the page is loaded
      this.showInProgress();
      this.dataprovider.getHarvestMouseList(
         tabConfig.filterString
      ).subscribe(
         data => {
            let the_data = <HarvestMouse[]>JSON.parse(<string>data)['mouse_list'];
            tabConfig.harvestMouseList = the_data;
            if (!tabConfig.harvestMouseList) {
               let the_data: HarvestMouse = <HarvestMouse>JSON.parse(<string>data);
               tabConfig.harvestMouseList = [];
               tabConfig.harvestMouseList.push(the_data);
            }

            tabConfig.datasource = new MatTableDataSource<HarvestMouse>(
               tabConfig.harvestMouseList);
            tabConfig.tabComponent.InsertDataSource(tabConfig.datasource);
            tabConfig.tabComponent.refreshSelected();
            this.trackedLoadedTabCom = this.trackedLoadedTabCom + 1;
            if (this.trackedLoadedTabCom == this.tabList.length) {
               this.toastservice.openSnackBar(
                  this._snackBar, 'Loaded list completed', 'Dismiss', SuccessColor
               )
            }

            this.InProgressDone();
         },
         error => {
            this.toastservice.openSnackBar(
               this._snackBar, 'Loading list failed', 'Dismiss', ErrorColor
            )
         }
      );
   }

   /*
   Funtion name: selectedTabChange
   Description: This function will be triggered when the switching to the new tab
   */
   selectedTabChange(event: MatTabChangeEvent) {
      if (event.tab) {
         let tabName = event.tab.textLabel;
         this.tabConfig.forEach(
            tabConfigEle => {
               if (tabConfigEle.tabName == tabName) {
                  this.activeTabConfig = tabConfigEle;
                  this.selectionEventTrigger(this.activeTabConfig.tabComponent.getSelectedRows());
                  this.activeTabConfig.tabComponent.refreshSelected();
               }
            }
         )
      }

   }

   /*
   Funtion name: openBottomSheetClick
   Description: This function will be triggered when the bottom sheet open button
                is clicked
   */
   openBottomSheetClick() {
      this.bottomsheetservice.openBottomSheet(
         this.bottomSheet,
         this.activeTabConfig.tabComponent.displayedColumnInfo,
         this.activeTabConfig.tabComponent.displayedColumns
      )
   }

   selectionEventTrigger(harvestdMouse) {
      this.selectedHarvestedMouse = harvestdMouse.selected;

      if (this.selectedHarvestedMouse &&
         this.selectedHarvestedMouse.length > 0) {
         this.groupSelectedEnabled = true;
      }
      else {
         this.groupSelectedEnabled = false;
      }
   }

   GroupDeleted() {
      this.diagservice.openConfirmationDialog(
         this.diaglog,
         this.selectedHarvestedMouse
      ).subscribe(result => {
         if (result) {
            this.showInProgress();
            this.dataprovider.deleteHarvestedMouseRequest(
               this.selectedHarvestedMouse
            ).subscribe(
               data => {
                  this.refreshTabAndData();
                  this.toastservice.openSnackBar(
                     this._snackBar,
                     "Deleted successfully",
                     "Dismiss",
                     SuccessColor
                  )
                  this.groupSelectedEnabled = false;
                  this.InProgressDone();
               },
               error => {
                  this.toastservice.openSnackBar(
                     this._snackBar,
                     "Encountered Error",
                     "Dismiss",
                     ErrorColor
                  )
                  this.InProgressDone();
               }
            )
         }
      });
   }

   showInProgress() {
      this.loaded = true;
   }

   InProgressDone() {
      this.loaded = false;
   }
}
