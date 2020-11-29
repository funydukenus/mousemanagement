import { TestBed } from '@angular/core/testing';

import { DiagService } from './diag.service';

describe('DiagService', () => {
  let service: DiagService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DiagService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
