import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { DataproviderService, harvestMouseFileUploadUrl } from '../service/dataprovider.service';
import { EventEmiterService } from '../service/event.emmiter.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ToastmessageService, SuccessColor, ErrorColor } from '../service/toastmessage.service';

@Component({
  selector: 'app-uploadcsvpage',
  templateUrl: './uploadcsvpage.component.html',
  styleUrls: ['./uploadcsvpage.component.scss']
})
export class UploadcsvpageComponent implements OnInit {
  // Reference the fileInput html element in the template
  @ViewChild('fileInput') fileInputButton: ElementRef;

  loaded: boolean;

  constructor(
    private dataprovider: DataproviderService,
    private _eventEmiter: EventEmiterService,
    private toastservice: ToastmessageService,
    private _snackBar: MatSnackBar,
  ) {
    this._eventEmiter.informPageLoc('uploadcsvpage');

    this._eventEmiter.dataStr.subscribe(
      data => {
        this.uploadButtonClick();
      }
    );
  }

  ngOnInit(): void {
  }

  /*
  Function name: fileInputChange
  Description: This is the callback function when the input file event
  changed is triggered
  */
  fileInputChange(event: any) {
    let file: File = event.target.files[0];
    this.showInProgress();
    this.dataprovider.fileUploadRequest(file, harvestMouseFileUploadUrl).subscribe(
      data => {
        this.toastservice.openSnackBar(
          this._snackBar, 'Imported Success', 'Dismiss', SuccessColor
        )
        this.fileInputButton.nativeElement.value = "";
        this.inProgressDone();
      },
      error => {
        this.toastservice.openSnackBar(
          this._snackBar, 'Something wrong', 'Dismiss', ErrorColor
        )
        // clear the file cache
        this.fileInputButton.nativeElement.value = "";
        this.inProgressDone();
      }
    );
  }

  /*
  Function name: uploadButtonClick
  Description: This is the callback function when the button is clicked
  to mimic the file upload input event
  */
  uploadButtonClick() {
    if (this.fileInputButton) {
      this.fileInputButton.nativeElement.click();
    }
  }

  showInProgress() {
    this.loaded = true;
  }

  inProgressDone() {
    this.loaded = false;
  }
}
