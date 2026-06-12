permissionset 51100 "ESM BASIC"
{
    Assignable = true;
    Caption = 'ESM BASIC';

    Permissions =
    tabledata Skill = R,
    tabledata "Skill Category" = R,
    tabledata "Employee Skill Assessment" = R,
    page "Skill List" = X,
    page "Skill Card" = X,
    page "Skill Category List" = X,
    page "Employee Skill Profile" = X,
    page "Empl. Skill Asmt. History" = X;
}
