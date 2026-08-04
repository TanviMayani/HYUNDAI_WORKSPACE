export function countTrueByType(jsonString) {
  const obj = JSON.parse(jsonString);
  let readOnly = 0;
  let fullAccess = 0;
  Object.values(obj).forEach((item) => {
    if (item && typeof item === "object") {
      if (item.read_only === true) readOnly++;
      if (item.full_access === true) fullAccess++;
    }
  });
  return { readOnly, fullAccess };
}
