import { Component, OnInit } from '@angular/core';
import { Validators } from '@angular/forms';
import { FormBuilder } from '@angular/forms';
import { FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { DataproviderService } from '../service/dataprovider.service';
import { EventEmiterService } from '../service/event.emmiter.service';
import { ErrorColor, SuccessColor, ToastmessageService } from '../service/toastmessage.service';

@Component({
   selector: 'app-updatepwdnewuser',
   templateUrl: './updatepwdnewuser.component.html',
   styleUrls: ['./updatepwdnewuser.component.scss']
})
export class UpdatepwdnewuserComponent implements OnInit {

   // Reference to the form object
   form: FormGroup;
   hasUserClickedSubmit: Boolean = false;

   // Reference submit button
   submitButtonTxt: string = "Update";

   // username and password field attribute
   WarningTxt: string = 'Username cannot be empty';
   AbnormalDetected: Boolean = false;
   passwordValue: string = '';

   // Loading trigger indication
   IsLoading: Boolean = false;

   triggered: Boolean = true;

   IsValid: Boolean = false;

   // Save current new user info
   secret_key: string;
   username: string;

   redirecedTimer;

   constructor(
      private activatedRoute: ActivatedRoute,
      private _router: Router,
      private _eventEmiter: EventEmiterService,
      private formBuilder: FormBuilder,
      private dataprovider: DataproviderService,
      private _snackBar: MatSnackBar,
      private toastservice: ToastmessageService) {
      this._eventEmiter.informPageLoc(
         'updatenewuser'
      );
      this.activatedRoute.queryParams.subscribe(params => {
         let secret_key = params['secret_key'];
         let username = params['username'];
         this.secret_key = secret_key;
         this.username = username;
         this.dataprovider.CheckSecretKey(secret_key, username).subscribe(
            result => {
               this.IsValid = true;
            },

            error => {
               this._router.navigate(['/pagenotfound']);
            }
         );
      });
   }

   ngOnInit(): void {
      // Setup FormControl for input validation
      this.form = this.formBuilder.group({
         password: [null, Validators.required]
      });

      // Setup observer for value change event
      this.form.valueChanges.subscribe(
         userForm => {
            this.resetAllValidation();
            this.passwordValue = userForm.password;
         }
      )
   }

   /*
   Function name: OnClickSubmit
   Description: This function trigger when the sumbit button is clicked
    */
   OnClickSubmit(data) {
      this.hasUserClickedSubmit = true;
      if (this.form.valid) {
         this.submitButtonTxt = "Updating...";
         this.IsLoading = true;
         this.dataprovider.NewUserChangePassword(
            this.secret_key,
            this.username,
            this.passwordValue,
         ).subscribe(
            result => {
               this.IsLoading = false;
               this.submitButtonTxt = "Done";
               this.toastservice.openSnackBar(
                  this._snackBar, 'Success! Redirected to login page in 3s', 'Dismiss', SuccessColor
               )
               setTimeout(() => {
                  this._router.navigate(['/login']);
               }, 3000)
            },
            error => {
               this.IsLoading = false;
               this.submitButtonTxt = "Update";
               if (error.status == 401) {
                  this.toastservice.openSnackBar(
                     this._snackBar, 'Username or Secrete is incorrect', 'Dismiss', ErrorColor
                  )
               }
            }
         )
      }
      else {
         if (!this.passwordValue) {
            this.WarningTxt = "Password cannot be empty";
            this.AbnormalDetected = true;
         }
      }
   }

   /*
   Function name: resetAllValidation
   Description: Reset all the attributes for input abnormal detection
    */
   resetAllValidation() {
      this.AbnormalDetected = false;
      this.hasUserClickedSubmit = false;
   }
}
