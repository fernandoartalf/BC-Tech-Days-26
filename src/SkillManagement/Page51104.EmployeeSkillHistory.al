page 51104 "Empl. Skill Asmt. History"
{
    ApplicationArea = All;
    Caption = 'Employee Skill Assessment History';
    Editable = false;
    PageType = List;
    SourceTable = "Employee Skill Assessment";
    SourceTableView = sorting("Employee No.", "Skill Code", "Effective Date") order(Descending);
    UsageCategory = None;

    layout
    {
        area(Content)
        {
            repeater(History)
            {
                field("Skill Code"; Rec."Skill Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the code of the skill.';
                }
                field("Proficiency Level"; Rec."Proficiency Level")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the assessed proficiency level for this skill.';
                }
                field("Effective Date"; Rec."Effective Date")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the date from which this assessment is effective.';
                }
                field(Status; Rec.Status)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies whether this assessment is confirmed or pending confirmation.';
                }
                field("Created By"; Rec."Created By")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the user who created this assessment.';
                }
                field("Created DateTime"; Rec."Created DateTime")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies when this assessment was created.';
                }
                field("Confirmed By"; Rec."Confirmed By")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the user who confirmed this assessment.';
                }
                field("Confirmed DateTime"; Rec."Confirmed DateTime")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies when this assessment was confirmed.';
                }
            }
        }
    }
}
