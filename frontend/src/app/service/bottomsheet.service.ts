import { Injectable } from '@angular/core';
import { Component } from '@angular/core';
import { Inject } from '@angular/core';
import { MatBottomSheet, MatBottomSheetRef } from '@angular/material/bottom-sheet';
import { ColumnInfo } from '../interface/columninfo';
import { MAT_BOTTOM_SHEET_DATA } from '@angular/material/bottom-sheet';

@Injectable({
   providedIn: 'root'
})
export class BottomsheetService {

   constructor() { }

   openBottomSheet(
      bottomSheet: MatBottomSheet,
      columnInfoList: ColumnInfo[],
      columnInfoString: string[]): void {
      bottomSheet.open(
         BottomSheetColSelComponent,
         { data: { colInfoList: columnInfoList, colList: columnInfoString } }
      );
   }
}


@Component({
   selector: 'bottom-sheet-col-sel-component',
   templateUrl: 'bottom-sheet-col-sel-component.html',
})
export class BottomSheetColSelComponent {
   colInfoList: ColumnInfo[];
   colList: string[];
   constructor(
      private _bottomSheetRef: MatBottomSheetRef<BottomSheetColSelComponent>,
      @Inject(MAT_BOTTOM_SHEET_DATA) public data: any) {
      console.log(data.colInfoList);
      this.colInfoList = data.colInfoList;
      this.colList = data.colList;
   }

   /*
   Funtion name: checkBoxChangedEventTrigger
   Description: This function will be triggered checkbox was checked or unchecked.
   */
   checkBoxChangedEventTrigger() {
      let hiddenColList: string[] = []
      this.colInfoList.forEach(
         colInfo => {
            if (!colInfo.display) {
               const index = this.colList.indexOf(colInfo.columnaName);
               if (index > -1) {
                  this.colList.splice(index, 1);
               }
            }
            else {
               const index = this.colList.indexOf(colInfo.columnaName);
               if (index == -1) {
                  this.colList.push(colInfo.columnaName);
               }
            }
         }
      )
   }
}
