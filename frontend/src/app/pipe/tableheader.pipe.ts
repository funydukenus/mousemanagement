import { Injectable, Pipe, PipeTransform } from '@angular/core';

interface columnDisplay{
   key: string,
   display: string
}

@Pipe({ name: 'tableheaderconverter' })

export class TableHeaderConverter implements PipeTransform {
   // columns of the table
   displayedColumns: columnDisplay[] = [
      {
         key: 'position',
         display: 'Position'
      },
      {
         key: 'handler',
         display: 'Handled By'
      },
      {
         key: 'physical_id',
         display: 'Physical ID'
      },
      {
         key: 'mouseline',
         display: 'MouseLine'
      },
      {
         key: 'gender',
         display: 'Gender'
      },
      {
         key: 'genotype',
         display: 'GenoType'
      },
      {
         key: 'birth_date',
         display: 'BirthDate'
      },
      {
         key: 'end_date',
         display: 'EndDate'
      },
      {
         key: 'cog',
         display: 'COG'
      },
      {
         key: 'phenotype',
         display: 'PhenoType'
      },
      {
         key: 'project_title',
         display: 'ProjectTitle'
      },
      {
         key: 'experiment',
         display: 'Experiment'
      },
      {
         key: 'comment',
         display: 'Comment'
      }
   ]

   /*
   Function name: transform
   Description: A pipe transformation used in the harvestMouseTable
                to convert each of header to respective display column header
   */
   transform(text: string[]): columnDisplay[]{
      return this.displayedColumns;
   }
} 