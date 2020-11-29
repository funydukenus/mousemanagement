import { Injectable } from '@angular/core';
import { DialogConfirmationComponent, DialogSimpleConfirmationComponent, DialogSingleEditComponent } from '../dialog/dialog.component';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HarvestMouse } from '../interface/harvestmouse';
import { Observable } from 'rxjs';

@Injectable({
   providedIn: 'root'
})
export class DiagService {

   constructor() { }

   openConfirmationDialog(
      diag: MatDialog,
      harvestmouse: HarvestMouse[]): Observable<any> {
      const dialogRef = diag.open(DialogConfirmationComponent, {
         width: '400px',
         data: { harvestedMouse: harvestmouse }
      });

      return dialogRef.afterClosed();
   }

   openSimpleConfirmationDialog(
      diag: MatDialog): Observable<any> {
      const dialogRef = diag.open(DialogSimpleConfirmationComponent, {
         width: '400px'
      });

      return dialogRef.afterClosed();
   }

   openSingleEditDialog(
      diag: MatDialog,
      harvestmouse: HarvestMouse): Observable<any> {
      const dialogRef = diag.open(DialogSingleEditComponent, {
         width: '900px',
         data: { harvestedMouse: harvestmouse }
      });

      return dialogRef.afterClosed();
   }
}
