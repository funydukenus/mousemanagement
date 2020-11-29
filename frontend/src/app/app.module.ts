import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MainpageComponent } from './mainpage/mainpage.component';
import { HarvestmousepageComponent } from './harvestmousepage/harvestmousepage.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { GenderConverter } from './pipe/gender.pipe';
import { TableHeaderConverter } from './pipe/tableheader.pipe';

// Import UI Related module
import { MatGridListModule } from '@angular/material/grid-list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { HarvestmousetabpageComponent } from './harvestmousetabpage/harvestmousetabpage.component';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from "@angular/material/core";
import { MatExpansionModule } from '@angular/material/expansion';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';

import { BottomSheetColSelComponent } from './service/bottomsheet.service';
import { DialogConfirmationComponent, DialogSimpleConfirmationComponent, DialogSingleEditComponent } from './dialog/dialog.component';
import { ReactiveFormsModule } from '@angular/forms';

import { EventEmiterService } from './service/event.emmiter.service';
import { LoginpageComponent } from './loginpage/loginpage.component';
import { UpdatepwdnewuserComponent } from './updatepwdnewuser/updatepwdnewuser.component';
import { PageNotFoundComponentComponent } from './page-not-found-component/page-not-found-component.component';
import { UploadcsvpageComponent } from './uploadcsvpage/uploadcsvpage.component';
import { UsermanagementpageComponent } from './usermanagementpage/usermanagementpage.component';

@NgModule({
   declarations: [
      AppComponent,
      MainpageComponent,
      HarvestmousepageComponent,
      GenderConverter,
      HarvestmousetabpageComponent,
      BottomSheetColSelComponent,
      TableHeaderConverter,
      DialogConfirmationComponent,
      DialogSimpleConfirmationComponent,
      DialogSingleEditComponent,
      LoginpageComponent,
      UpdatepwdnewuserComponent,
      PageNotFoundComponentComponent,
      UploadcsvpageComponent,
      UsermanagementpageComponent
   ],
   imports: [
      BrowserModule,
      AppRoutingModule,
      BrowserAnimationsModule,
      FormsModule,
      MatGridListModule,
      MatToolbarModule,
      HttpClientModule,
      MatTableModule,
      MatSortModule,
      MatPaginatorModule,
      MatFormFieldModule,
      MatInputModule,
      MatSnackBarModule,
      MatTabsModule,
      MatProgressBarModule,
      DragDropModule,
      MatBottomSheetModule,
      MatCheckboxModule,
      MatDialogModule,
      MatSelectModule,
      MatDatepickerModule,
      MatNativeDateModule,
      MatExpansionModule,
      MatAutocompleteModule,
      MatIconModule,
      MatSidenavModule,
      MatListModule,
      ReactiveFormsModule,
   ],
   providers: [EventEmiterService],
   bootstrap: [AppComponent]
})
export class AppModule { }
