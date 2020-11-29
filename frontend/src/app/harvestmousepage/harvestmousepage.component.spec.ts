import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HarvestmousepageComponent } from './harvestmousepage.component';

describe('HarvestmousepageComponent', () => {
   let component: HarvestmousepageComponent;
   let fixture: ComponentFixture<HarvestmousepageComponent>;

   beforeEach(async(() => {
      TestBed.configureTestingModule({
         declarations: [HarvestmousepageComponent]
      })
         .compileComponents();
   }));

   beforeEach(() => {
      fixture = TestBed.createComponent(HarvestmousepageComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();
   });

   it('should create', () => {
      expect(component).toBeTruthy();
   });
});
