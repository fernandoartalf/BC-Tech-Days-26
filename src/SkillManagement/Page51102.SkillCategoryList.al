page 51102 "Skill Category List"
{
    ApplicationArea = All;
    Caption = 'Skill Categories';
    PageType = List;
    SourceTable = "Skill Category";
    UsageCategory = Lists;

    layout
    {
        area(Content)
        {
            repeater(SkillCategories)
            {
                field(Code; Rec.Code)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies the unique code that identifies the skill category.';
                }
                field(Description; Rec.Description)
                {
                    ApplicationArea = All;
                    ToolTip = 'Specifies a description of the skill category.';
                }
            }
        }
    }
}
