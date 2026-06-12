page 51103 "Employee Skill Profile"
{
    ApplicationArea = All;
    Caption = 'Skill Profile';
    PageType = ListPart;
    SourceTable = "Employee Skill Assessment";

    layout
    {
        area(Content)
        {
            repeater(SkillProfile)
            {
                field("Skill Code"; Rec."Skill Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the code of the skill.';
                }
                field(SkillDescription; SkillDescription)
                {
                    ApplicationArea = All;
                    Caption = 'Skill Description';
                    Editable = false;
                    ToolTip = 'Specifies the description of the skill.';
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
                    Editable = false;
                    StyleExpr = StatusStyle;
                    ToolTip = 'Specifies whether this assessment is confirmed or pending confirmation.';
                }
            }
        }
    }

    actions
    {
        area(Processing)
        {
            action(ConfirmAssessment)
            {
                ApplicationArea = All;
                Caption = 'Confirm';
                Image = Approve;
                ToolTip = 'Confirms the selected pending skill assessment.';
                Visible = IsESMFull;

                trigger OnAction()
                var
                    SkillMgt: Codeunit "Skill Mgt.";
                begin
                    SkillMgt.ConfirmAssessment(Rec."Entry No.");
                    CurrPage.Update(false);
                end;
            }
        }
    }

    var
        StatusStyle: Text;
        SkillDescription: Text[100];
        IsESMFull: Boolean;

    trigger OnOpenPage()
    var
        SkillMgt: Codeunit "Skill Mgt.";
    begin
        IsESMFull := SkillMgt.UserHasESMFullPermission();
    end;

    trigger OnNewRecord(BelowxRec: Boolean)
    begin
        if IsESMFull then
            Rec.Status := "Skill Assessment Status"::Confirmed
        else
            Rec.Status := "Skill Assessment Status"::"Pending Confirmation";
        Rec."Effective Date" := WorkDate();
    end;

    trigger OnAfterGetRecord()
    var
        Skill: Record Skill;
    begin
        Skill.SetLoadFields(Description);
        if Skill.Get(Rec."Skill Code") then
            SkillDescription := Skill.Description
        else
            SkillDescription := '';

        if Rec.Status = "Skill Assessment Status"::"Pending Confirmation" then
            StatusStyle := 'Ambiguous'
        else
            StatusStyle := '';
    end;
}
