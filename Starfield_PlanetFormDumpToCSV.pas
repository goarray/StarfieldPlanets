{
  Starfield_PlanetFormDumpToCSV.pas
  Exports all selected planet records to PlanetsDump.csv for later processing.
  Empty field names -> Signature or 'Unknown'; empty values -> Name or 'None'.
   Certain known elements (e.g., Houdini BFCB) are skipped.
}
unit Starfield_FormDumpToCSV;

var
  csvLines: TStringList;

function Initialize: Integer;
begin
  csvLines := TStringList.Create;
  csvLines.Add('EditorID,Path,Field Name,Signature,Value');
  Result := 0;
end;

procedure ProcessSubrecords(e: IInterface; const editorID: string; const path: string);
var
  i: Integer;
  child: IInterface;
  fieldName, fieldSignature, fieldValue: string;
  currentPath: string;
begin
  for i := 0 to ElementCount(e) - 1 do begin
    child := ElementByIndex(e, i);
    // HARD SKIP: Houdini Base Form Component, Blows up the CSV otherwise!
    if (Signature(child) = 'BFCB') and
       (GetEditValue(child) = 'HoudiniData_Component') then
      Exit; // abort processing this entire Component #n branch
        if not Assigned(child) then Continue;

    fieldName := DisplayName(child);
    if fieldName = '' then fieldName := Signature(child);
    if fieldName = '' then fieldName := 'Unknown';

    fieldSignature := Signature(child);
    if (fieldSignature = '') or (Length(fieldSignature) > 4) then
      fieldSignature := 'Unknown';

    try
      fieldValue := GetEditValue(child);
      if fieldValue = '' then fieldValue := Name(child);
    except
      fieldValue := 'Non-editable';
    end;

    fieldValue := StringReplace(fieldValue, ',', ';', [rfReplaceAll]);

    if path = '' then
      currentPath := fieldName
    else
      currentPath := path + '>' + fieldName;

    csvLines.Add(Format('%s,%s,%s,%s,%s',
      [editorID, currentPath, fieldName, fieldSignature, fieldValue]
    ));

    if ElementCount(child) > 0 then
      ProcessSubrecords(child, editorID, currentPath);
  end;
end;

function GetRecordIdentifier(e: IInterface): string;
var
  edid: string;
begin
  edid := GetElementEditValues(e, 'EDID');
  if edid = '' then
    edid := '_AutoFormID_' + IntToHex(GetLoadOrderFormID(e), 8);
  Result := edid;
end;

function Process(e: IInterface): Integer;
var
  recordID: string;
begin
  recordID := GetRecordIdentifier(e);
  //log message
  AddMessage('Processing record: ' + recordID);
  ProcessSubrecords(e, recordID, Name(e));
  Result := 0; // Important for batch mode
end;

function Finalize: Integer;
var
  filePath: string;
begin
  filePath := ProgramPath + 'PlanetsDump.csv';
  try
    csvLines.SaveToFile(filePath);
    AddMessage('CSV Output Saved: ' + filePath);
  except
    AddMessage('Error saving CSV file: ' + filePath);
  end;
  csvLines.Free;
  Result := 0;
end;

end.

