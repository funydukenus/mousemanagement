import { TestBed } from '@angular/core/testing';

import { BottomsheetService } from './bottomsheet.service';

describe('BottomsheetService', () => {
  let service: BottomsheetService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BottomsheetService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
