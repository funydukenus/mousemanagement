import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HarvestmousetabpageComponent } from './harvestmousetabpage.component';

describe('HarvestmousetabpageComponent', () => {
  let component: HarvestmousetabpageComponent;
  let fixture: ComponentFixture<HarvestmousetabpageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HarvestmousetabpageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HarvestmousetabpageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
