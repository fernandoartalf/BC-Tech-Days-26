page 51100 "Skill List"
{
    ApplicationArea = All;
    Caption = 'Skills';
    CardPageID = "Skill Card";
    PageType = List;
    SourceTable = Skill;
    UsageCategory = Lists;

    layout
    {
        area(Content)
        {
            repeater(Skills)
            {
                field(Code; Rec.Code)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the unique code that identifies the skill.';
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies a description of the skill.';
                }
                field("Category Code"; Rec."Category Code")
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the category this skill belongs to.';
                }
                field(Blocked; Rec.Blocked)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies whether the skill is blocked and cannot be added to new employee assessments.';
                }
            }
        }
    }

    trigger OnOpenPage()
    begin
        Rec.SetRange(Blocked, false);
    end;
}
