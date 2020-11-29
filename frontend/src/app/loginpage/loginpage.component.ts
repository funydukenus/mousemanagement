import { Component, OnInit,OnChanges, ViewEncapsulation } from '@angular/core';
import { EventEmiterService } from '../service/event.emmiter.service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { DataproviderService } from '../service/dataprovider.service';
import { ToastmessageService, ErrorColor } from '../service/toastmessage.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';

@Component({
   selector: 'app-loginpage',
   templateUrl: './loginpage.component.html',
   styleUrls: ['./loginpage.component.scss'],
   encapsulation: ViewEncapsulation.None
})
export class LoginpageComponent implements OnInit {

   // Reference to the form object
   form: FormGroup;
   hasUserClickedSubmit: Boolean = false;

   // Reference submit button
   submitButtonTxt: string = "Get Me In";

   // username and password field attribute
   WarningTxt: string = 'Username cannot be empty';
   AbnormalDetected: Boolean = false;
   usernameValue: string = '';
   passwordValue: string = '';

   // Loading trigger indication
   IsLoading: Boolean = false;

   triggered: Boolean = true;

   constructor(
      private _router: Router,
      private _eventEmiter: EventEmiterService,
      private formBuilder: FormBuilder,
      private dataprovider: DataproviderService,
      private _snackBar: MatSnackBar,
      private toastservice: ToastmessageService) {
      this._eventEmiter.informPageLoc(
         'login'
      );
   }

   ngOnInit(): void {

      // Setup FormControl for input validation
      this.form = this.formBuilder.group({
         username: [null, [Validators.required]],
         password: [null, Validators.required],
      });

      // Setup observer for value change event
      this.form.valueChanges.subscribe(
         userForm => {
            this.resetAllValidation();
            this.usernameValue = userForm.username;
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
         this.submitButtonTxt = "Validating...";
         this.IsLoading = true;
         this.dataprovider.ValidateUserInfo(
            this.usernameValue,
            this.passwordValue
         )
         
         .subscribe(
            (result) => {
                  console.log(result);
               this.IsLoading = false;
               this.submitButtonTxt = "Done";
               localStorage.setItem('username', this.usernameValue);
               this._router.navigate(['/home']);
            },
            (error) => {
               this.IsLoading = false;
               this.submitButtonTxt = "Get Me In";
               if (error.status == 401) {
                  this.toastservice.openSnackBar(
                     this._snackBar, 'Username or Password is incorrect', 'Dismiss', ErrorColor
                  )
               }
            }
         )
      }
      else {
         if (!this.usernameValue || !this.passwordValue) {
            this.WarningTxt = "Username or Password cannot be empty";
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
