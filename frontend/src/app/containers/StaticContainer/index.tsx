import Grid from "@mui/material/Grid";
import { Stack, useTheme } from "@mui/material";
import backgroundImage from "../../../assets/images/auth/AuthSide.svg";
import logo from "../../../assets/binaryLogo.svg";

export default function StaticContainer({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme = useTheme();
  return (
    <Grid container width={"100%"} height={"100%"}>
      <Grid
        item
        md={0}
        justifyContent={"center"}
        sx={{ mx: "auto", my: 4, display: { md: "none" }, height: "0px" }}
      >
        <img src={logo} alt="Binary Sematics" />
      </Grid>
      <Grid
        item
        xs={0}
        md={6}
        sx={{
          backgroundColor: theme.palette.secondary.main,
          backgroundImage: `url(${backgroundImage})`,
          backgroundRepeat: "no-repeat",
          backgroundSize: "cover",
        }}
      ></Grid>
      <Grid item xs={12} md={6}>
        <Stack direction="row" justifyContent={"center"} height={"100%"}>
          {children}
        </Stack>
      </Grid>
    </Grid>
  );
}
