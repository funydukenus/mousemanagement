import { Component, ViewChild } from '@angular/core';
import { EventEmiterService } from './service/event.emmiter.service';
import { MatDrawer } from '@angular/material/sidenav';
import { DataproviderService } from './service/dataprovider.service';
import { Router, NavigationEnd } from '@angular/router';


@Component({
   selector: 'app-root',
   templateUrl: './app.component.html',
   styleUrls: ['./app.component.scss']
})
export class AppComponent {
   title = 'mousemanagementsite';

   // Indicate which page it is
   // it will be signal when the target page is reached
   type: string = 'login';

   // Reference to the side bar of the html page
   @ViewChild('sidenav') sideNav: MatDrawer;

   // Indicate that the user account validation has done
   ValidationDone: Boolean = false;

   constructor(
      private _eventEmiter: EventEmiterService,
      private dataprovider: DataproviderService,
      private _router: Router
   ) {
      this._router.events.subscribe(
         (event) => {
            // Checks validation each time the router event occurs
            if (event instanceof NavigationEnd) {
               let NeedChecking: Boolean = true;
               if (event.url.includes('secret_key')) {
                  let s = event.url.substr(0, event.url.indexOf('?secret_key'));
                  if (s === '/updatepwdnewuser') {
                     NeedChecking = false;
                  }
               }

               if (event.url.includes('pagenotfound')) {
                  NeedChecking = false;
               }

               if (NeedChecking) {
                  this.dataprovider.CheckIsLogin().subscribe(
                     result => {
                        this.ValidationDone = true;
                     },
                     error => {
                        this.returnToLoginPage();
                     }
                  );
               }
            }
         });

      // Setup the call back function
      // to each to the page indicator source
      this._eventEmiter.pageLocIndicator.subscribe(
         data => {
            this.ModifySideBarChoice(data);
         }
      )
   }

   returnToLoginPage() {
      this.ValidationDone = false;
      this._router.navigate(['/login']);
      this._eventEmiter.informPageLoc(
         'login'
      );
   }

   UploadClick() {
      this._eventEmiter.sendMessage();
      this.sideNav.close();
   }

   Logout() {
      this.dataprovider.UserLoggout().subscribe(
         result => {
            localStorage.setItem('username', '');
            this.ValidationDone = false;
            this._router.navigate(['/login']);
         },
         error => {
            console.log(error);
         }
      )
   }

   ModifySideBarChoice(inputType) {
      if (this.type !== inputType) {
         this.type = inputType;
      }
   }

   IsMainPage() {
      return this.type === 'main';
   }

   IsHarvestMousePage() {
      return this.type === 'mousetable';
   }

   IsLoginPage() {
      return this.type === 'login';
   }

   IsUpdateNewUser() {
      return this.type === 'updatenewuser';
   }

   ShowSideBar() {
      return !(this.IsLoginPage() || this.IsUpdateNewUser())
   }
}
