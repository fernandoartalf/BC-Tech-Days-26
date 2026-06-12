table 51100 Skill
{
    Caption = 'Skill';
    DrillDownPageID = "Skill List";
    LookupPageID = "Skill List";

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
        field(3; "Category Code"; Code[20])
        {
            Caption = 'Category Code';
            DataClassification = CustomerContent;
            TableRelation = "Skill Category".Code;
        }
        field(4; Blocked; Boolean)
        {
            Caption = 'Blocked';
            DataClassification = CustomerContent;
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
        SkillMgt: Codeunit "Skill Mgt.";
    begin
        SkillMgt.CanDeleteSkill(Rec.Code);
    end;
}
