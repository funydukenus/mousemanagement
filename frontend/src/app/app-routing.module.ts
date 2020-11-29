import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainpageComponent } from './mainpage/mainpage.component';
import { HarvestmousetabpageComponent } from './harvestmousetabpage/harvestmousetabpage.component';
import { LoginpageComponent } from './loginpage/loginpage.component';
import { UpdatepwdnewuserComponent } from './updatepwdnewuser/updatepwdnewuser.component';
import { PageNotFoundComponentComponent } from './page-not-found-component/page-not-found-component.component';
import { UploadcsvpageComponent } from './uploadcsvpage/uploadcsvpage.component';
import { UsermanagementpageComponent } from './usermanagementpage/usermanagementpage.component';

const routes: Routes = [
   {
      path: 'home',
      component: MainpageComponent
   },
   {
    path: 'harvest-mouse',
    component: HarvestmousetabpageComponent
   },
   {
    path: 'upload-csv',
    component: UploadcsvpageComponent
   },
   {
      path: 'login',
      component: LoginpageComponent
   },
   {
      path: 'updatepwdnewuser',
      component: UpdatepwdnewuserComponent
   },
   {
      path: 'user-management-page',
      component: UsermanagementpageComponent
   },
   {
      path: 'pagenotfound',
      component: PageNotFoundComponentComponent
   },
   {
      path: '',
      redirectTo: '/home',
      pathMatch: 'full'
   }
];

@NgModule({
   imports: [RouterModule.forRoot(routes)],
   exports: [RouterModule]
})
export class AppRoutingModule { }
