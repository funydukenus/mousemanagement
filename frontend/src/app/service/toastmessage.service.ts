import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';


export var SuccessColor: string = "green-snackbar";
export var ErrorColor: string = "red-snackbar";
export var InProgressColor: string = "yellow-snackbar";

@Injectable({
   providedIn: 'root'
})
export class ToastmessageService {

   constructor() { }

   /*
   Funtion name: openSnackBar
   Description: This function opens up the snack bar and disapear after 2s
   */
   openSnackBar(snackerBar: MatSnackBar, message: string, action: string, colorClass="blue-snackbar") {
      snackerBar.open(message, action, {
         duration: 2000,
         panelClass: [colorClass]
      });
   }
}