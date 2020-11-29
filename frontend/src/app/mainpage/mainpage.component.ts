import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

// Import UI Related module
import { interval } from 'rxjs';

import { EventEmiterService } from '../service/event.emmiter.service';

@Component({
   selector: 'app-mainpage',
   templateUrl: './mainpage.component.html',
   styleUrls: ['./mainpage.component.scss']
})
export class MainpageComponent implements OnInit {

   todayDate = new Date().toLocaleString();

   constructor(
      private _router: Router,
      private _eventEmiter: EventEmiterService) {
      this._eventEmiter.informPageLoc(
         'main'
      );

   }

   ngOnInit(): void {
      // Creates a timer to update the current datetime
      let sub = interval(1000).subscribe(x => {
         this.todayDate = new Date().toLocaleString();
      });
   }

   PageDirect(target){
      this._router.navigate([target]);
   }

   /*
   triggerGridEvent(routeLink: string): void {
      this._router.navigate([routeLink]);
   }
   */
}
