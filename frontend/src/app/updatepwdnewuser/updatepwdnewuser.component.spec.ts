import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdatepwdnewuserComponent } from './updatepwdnewuser.component';

describe('UpdatepwdnewuserComponent', () => {
  let component: UpdatepwdnewuserComponent;
  let fixture: ComponentFixture<UpdatepwdnewuserComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UpdatepwdnewuserComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UpdatepwdnewuserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
