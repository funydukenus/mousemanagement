import { Pipe, PipeTransform } from '@angular/core';
@Pipe({ name: 'genderConverter' })

export class GenderConverter implements PipeTransform {
   /*
   Function name: transform
   Description: A pipe transformation used in the harvestMouseTable
                to convert M to Male and F to Female
   */
   transform(gender: string): string {
      if (gender == 'M') {
         return 'Male';
      }
      else {
         return 'Female';
      }
   }
} 