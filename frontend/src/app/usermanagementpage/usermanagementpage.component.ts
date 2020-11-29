import { Component, OnInit } from '@angular/core';
import { EventEmiterService } from '../service/event.emmiter.service';

@Component({
   selector: 'app-usermanagementpage',
   templateUrl: './usermanagementpage.component.html',
   styleUrls: ['./usermanagementpage.component.scss']
})
export class UsermanagementpageComponent implements OnInit {

   constructor(
      private _eventEmiter: EventEmiterService
   ) {
      this._eventEmiter.informPageLoc(
         'usermanagement'
      );
   }

   ngOnInit(): void {
   }

}
