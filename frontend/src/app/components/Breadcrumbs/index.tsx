import { useLocation } from "react-router-dom";
import { Breadcrumbs, Typography } from "@mui/material";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";

function toTitleCase(str) {
  return str.replace(/\b\w+/g, function (s) {
    return s.charAt(0).toUpperCase() + s.substr(1).toLowerCase();
  });
}

export default function RouteBreadcrumb() {
  const location = useLocation();
  const pathnames = location.pathname.split("/").filter((x) => x);

  return (
    <Breadcrumbs
      aria-label="Breadcrumb"
      separator={<NavigateNextIcon fontSize="small" />}
    >
      {pathnames.map((value, index) => {
        const last = index === pathnames.length - 1;
        const to = `/${pathnames.slice(0, index + 1).join("/")}`;

        return last ? (
          <Typography color="textPrimary" key={to} variant="body2">
            {toTitleCase(value)}
          </Typography>
        ) : (
          <Typography color="textPrimary" key={to} variant="body2">
            {toTitleCase(value)}
          </Typography>
        );
      })}
    </Breadcrumbs>
  );
}
