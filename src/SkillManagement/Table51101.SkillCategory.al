table 51101 "Skill Category"
{
    Caption = 'Skill Category';
    DrillDownPageID = "Skill Category List";
    LookupPageID = "Skill Category List";

    fields
    {
        field(1; Code; Code[20])
        {
            Caption = 'Code';
            DataClassification = CustomerContent;
            NotBlank = true;
        }
        field(2; Description; Text[100])
        {
            Caption = 'Description';
            DataClassification = CustomerContent;
            NotBlank = true;
        }
    }

    keys
    {
        key(PK; Code)
        {
            Clustered = true;
        }
    }

    trigger OnDelete()
    var
        SkillRec: Record Skill;
        CannotDeleteCategoryErr: Label 'You cannot delete Skill Category %1 because one or more skills reference it.', Comment = '%1 = Category Code';
    begin
        SkillRec.SetRange("Category Code", Rec.Code);
        if not SkillRec.IsEmpty() then
            Error(CannotDeleteCategoryErr, Rec.Code);
    end;
}
