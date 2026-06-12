table 51102 "Employee Skill Assessment"
{
    Caption = 'Employee Skill Assessment';

    fields
    {
        field(1; "Entry No."; Integer)
        {
            AutoIncrement = true;
            Caption = 'Entry No.';
            DataClassification = CustomerContent;
        }
        field(2; "Employee No."; Code[20])
        {
            Caption = 'Employee No.';
            DataClassification = CustomerContent;
            NotBlank = true;
            TableRelation = Employee."No.";
        }
        field(3; "Skill Code"; Code[20])
        {
            Caption = 'Skill Code';
            DataClassification = CustomerContent;
            NotBlank = true;
            TableRelation = Skill.Code;
        }
        field(4; "Proficiency Level"; Enum "Skill Proficiency Level")
        {
            Caption = 'Proficiency Level';
            DataClassification = CustomerContent;
        }
        field(5; "Effective Date"; Date)
        {
            Caption = 'Effective Date';
            DataClassification = CustomerContent;
        }
        field(6; Status; Enum "Skill Assessment Status")
        {
            Caption = 'Status';
            DataClassification = CustomerContent;
        }
        field(7; "Created By"; Code[50])
        {
            Caption = 'Created By';
            DataClassification = EndUserIdentifiableInformation;
        }
        field(8; "Created DateTime"; DateTime)
        {
            Caption = 'Created DateTime';
            DataClassification = CustomerContent;
        }
        field(9; "Confirmed By"; Code[50])
        {
            Caption = 'Confirmed By';
            DataClassification = EndUserIdentifiableInformation;
        }
        field(10; "Confirmed DateTime"; DateTime)
        {
            Caption = 'Confirmed DateTime';
            DataClassification = CustomerContent;
        }
    }

    keys
    {
        key(PK; "Entry No.")
        {
            Clustered = true;
        }
        key(Key2; "Employee No.", "Skill Code", "Effective Date")
        {
        }
    }

    trigger OnInsert()
    begin
        Rec."Created By" := CopyStr(UserId(), 1, MaxStrLen(Rec."Created By"));
        Rec."Created DateTime" := CurrentDateTime();
    end;

    trigger OnModify()
    var
        AssessmentCannotBeModifiedErr: Label 'Employee Skill Assessments are immutable and cannot be modified.';
    begin
        Error(AssessmentCannotBeModifiedErr);
    end;

    trigger OnDelete()
    var
        AssessmentCannotBeDeletedErr: Label 'Employee Skill Assessments are immutable and cannot be deleted.';
    begin
        Error(AssessmentCannotBeDeletedErr);
    end;
}
