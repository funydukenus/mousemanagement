export interface PfaRecord{
   liver: number,
   liver_tumor: number,
   small_intenstine: number,
   small_intenstine_tumor: number,
   skin: number,
   skin_tumor: number,
   others: string
}

export interface FreezeRecord{
   liver: number,
   liver_tumor: number,
   others: string
}

export interface HarvestMouse{
   id: number,
   handler: string,
   physical_id: string,
   gender: string,
   mouseline: string,
   genotype: string,
   birth_date: string,
   end_date: string,
   cog: string,
   phenotype: string,
   project_title: string,
   experiment: string,
   comment: string,
   freeze_record: FreezeRecord,
   pfa_record: PfaRecord
}
