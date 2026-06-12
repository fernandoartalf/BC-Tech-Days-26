codeunit 51100 "Skill Mgt."
{
    /// <summary>
    /// Validates and inserts a new Employee Skill Assessment record.
    /// Errors if Employee or Skill do not exist, Skill is blocked, ProfLevel is Unassigned, or EffectiveDate is blank.
    /// </summary>
    procedure AddSkillAssessment(EmployeeNo: Code[20]; SkillCode: Code[20]; ProfLevel: Enum "Skill Proficiency Level"; EffectiveDate: Date; InitialStatus: Enum "Skill Assessment Status")
    var
        Employee: Record Employee;
        Skill: Record Skill;
        EmployeeSkillAssessment: Record "Employee Skill Assessment";
        EmployeeNotFoundErr: Label 'Employee %1 does not exist.', Comment = '%1 = Employee No.';
        SkillNotFoundErr: Label 'Skill %1 does not exist.', Comment = '%1 = Skill Code';
        SkillBlockedErr: Label 'Skill %1 is blocked and cannot be assigned to an employee.', Comment = '%1 = Skill Code';
        UnassignedProficiencyErr: Label 'Proficiency Level must not be Unassigned.';
        EffectiveDateBlankErr: Label 'Effective Date must have a value.';
    begin
        if not Employee.Get(EmployeeNo) then
            Error(EmployeeNotFoundErr, EmployeeNo);
        if not Skill.Get(SkillCode) then
            Error(SkillNotFoundErr, SkillCode);
        if Skill.Blocked then
            Error(SkillBlockedErr, SkillCode);
        if ProfLevel = "Skill Proficiency Level"::Unassigned then
            Error(UnassignedProficiencyErr);
        if EffectiveDate = 0D then
            Error(EffectiveDateBlankErr);

        EmployeeSkillAssessment.Init();
        EmployeeSkillAssessment."Employee No." := EmployeeNo;
        EmployeeSkillAssessment."Skill Code" := SkillCode;
        EmployeeSkillAssessment."Proficiency Level" := ProfLevel;
        EmployeeSkillAssessment."Effective Date" := EffectiveDate;
        EmployeeSkillAssessment.Status := InitialStatus;
        EmployeeSkillAssessment.Insert(true);
    end;

    /// <summary>
    /// Returns the most recent confirmed Proficiency Level for an employee's skill as of a given date.
    /// Returns Unassigned if no confirmed assessment exists on or before AsOfDate.
    /// </summary>
    procedure GetCurrentProficiency(EmployeeNo: Code[20]; SkillCode: Code[20]; AsOfDate: Date): Enum "Skill Proficiency Level"
    var
        EmployeeSkillAssessment: Record "Employee Skill Assessment";
    begin
        EmployeeSkillAssessment.SetLoadFields("Proficiency Level", "Effective Date");
        EmployeeSkillAssessment.SetCurrentKey("Employee No.", "Skill Code", "Effective Date");
        EmployeeSkillAssessment.SetRange("Employee No.", EmployeeNo);
        EmployeeSkillAssessment.SetRange("Skill Code", SkillCode);
        EmployeeSkillAssessment.SetRange(Status, "Skill Assessment Status"::Confirmed);
        EmployeeSkillAssessment.SetFilter("Effective Date", '..%1', AsOfDate);
        if EmployeeSkillAssessment.FindLast() then
            exit(EmployeeSkillAssessment."Proficiency Level");
        exit("Skill Proficiency Level"::Unassigned);
    end;

    /// <summary>
    /// Confirms a pending skill assessment. Requires the caller to hold the ESM FULL permission set.
    /// Uses ModifyAll to bypass the immutability guard in OnModify (ARCH-001 ADR-3).
    /// </summary>
    procedure ConfirmAssessment(EntryNo: Integer)
    var
        EmployeeSkillAssessment: Record "Employee Skill Assessment";
        AlreadyConfirmedErr: Label 'Assessment entry %1 is already confirmed.', Comment = '%1 = Entry No.';
        InsufficientPermissionsErr: Label 'You do not have sufficient permissions to confirm skill assessments. ESM FULL permission set is required.';
    begin
        if not UserHasESMFullPermission() then
            Error(InsufficientPermissionsErr);

        EmployeeSkillAssessment.Get(EntryNo);
        if EmployeeSkillAssessment.Status = "Skill Assessment Status"::Confirmed then
            Error(AlreadyConfirmedErr, EntryNo);

        EmployeeSkillAssessment.SetRange("Entry No.", EntryNo);
        EmployeeSkillAssessment.ModifyAll(EmployeeSkillAssessment.Status, "Skill Assessment Status"::Confirmed);
        EmployeeSkillAssessment.ModifyAll(EmployeeSkillAssessment."Confirmed By", CopyStr(UserId(), 1, 50));
        EmployeeSkillAssessment.ModifyAll(EmployeeSkillAssessment."Confirmed DateTime", CurrentDateTime());
    end;

    /// <summary>
    /// Sets the Blocked flag on a Skill record. Errors if the Skill does not exist.
    /// </summary>
    procedure BlockSkill(SkillCode: Code[20])
    var
        Skill: Record Skill;
        SkillNotFoundErr: Label 'Skill %1 does not exist.', Comment = '%1 = Skill Code';
    begin
        if not Skill.Get(SkillCode) then
            Error(SkillNotFoundErr, SkillCode);
        Skill.Validate(Blocked, true);
        Skill.Modify(true);
    end;

    /// <summary>
    /// Guards Skill deletion. Errors if any Employee Skill Assessment references the skill.
    /// Returns true when deletion is safe.
    /// </summary>
    procedure CanDeleteSkill(SkillCode: Code[20]): Boolean
    var
        EmployeeSkillAssessment: Record "Employee Skill Assessment";
        CannotDeleteSkillErr: Label 'You cannot delete Skill %1 because it has one or more employee skill assessments.', Comment = '%1 = Skill Code';
    begin
        EmployeeSkillAssessment.SetLoadFields("Skill Code");
        EmployeeSkillAssessment.SetRange("Skill Code", SkillCode);
        if not EmployeeSkillAssessment.IsEmpty() then
            Error(CannotDeleteSkillErr, SkillCode);
        exit(true);
    end;

    /// <summary>
    /// Returns true if the current user has the ESM FULL permission set assigned.
    /// Queries the Access Control table filtered by the current user's security ID.
    /// </summary>
    procedure UserHasESMFullPermission(): Boolean
    var
        AccessControl: Record "Access Control";
    begin
        AccessControl.SetRange("User Security ID", UserSecurityId());
        AccessControl.SetRange("Role ID", 'ESM FULL');
        exit(not AccessControl.IsEmpty());
    end;
}
