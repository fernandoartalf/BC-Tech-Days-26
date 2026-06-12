permissionset 51101 "ESM FULL"
{
    Assignable = true;
    Caption = 'ESM FULL';
    IncludedPermissionSets = "ESM BASIC";

    Permissions =
    tabledata Skill = RIMD,
    tabledata "Skill Category" = RIMD,
    tabledata "Employee Skill Assessment" = RI;
}
