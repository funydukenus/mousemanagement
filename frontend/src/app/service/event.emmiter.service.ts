import {Injectable, EventEmitter} from '@angular/core';

@Injectable()
export class EventEmiterService {

  dataStr = new EventEmitter();

  pageLocIndicator = new EventEmitter();

  constructor() { }

  sendMessage() {
    this.dataStr.emit();
  }

  informPageLoc(loc){
     this.pageLocIndicator.emit(loc);
  }

}