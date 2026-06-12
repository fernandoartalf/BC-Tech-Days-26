pageextension 51100 "Employee Card ESM Ext" extends "Employee Card"
{
    layout
    {
        addlast(FactBoxes)
        {
            part(EmployeeSkillProfile; "Employee Skill Profile")
            {
                ApplicationArea = All;
                Caption = 'Skill Profile';
                SubPageLink = "Employee No." = field("No.");
            }
        }
    }

    actions
    {
        addlast(Navigation)
        {
            action(SkillHistory)
            {
                ApplicationArea = All;
                Caption = 'Skill History';
                Image = History;
                RunObject = page "Empl. Skill Asmt. History";
                RunPageLink = "Employee No." = field("No.");
                ToolTip = 'View the complete skill assessment history for this employee.';
            }
        }
    }
}
