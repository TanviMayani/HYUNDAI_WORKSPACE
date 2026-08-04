import { Box, Grid, Paper } from "@mui/material";

const MainBox = ({ children }) => {
  return (
    <Paper
      elevation={0}
      className="defaultShadow defaultRadius"
      sx={{
        mx: 3,
        mb: 5,
        bgcolor: (theme) => theme.palette.common.white,
        maxHeight: "100%",
        minHeight: "10vh",
      }}
    >
      <Box
        sx={{
          background: (theme) => theme.palette.common.white,
          maxWidth: "100%",
        }}
      >
        <Grid
          container
          spacing={2}
          justifyContent={"start"}
          sx={{ mt: 1, px: 3 }}
        >
          {children}
        </Grid>
      </Box>
    </Paper>
  );
};

export default MainBox;




