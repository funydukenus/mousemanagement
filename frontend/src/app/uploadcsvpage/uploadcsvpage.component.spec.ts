import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadcsvpageComponent } from './uploadcsvpage.component';

describe('UploadcsvpageComponent', () => {
  let component: UploadcsvpageComponent;
  let fixture: ComponentFixture<UploadcsvpageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UploadcsvpageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadcsvpageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
