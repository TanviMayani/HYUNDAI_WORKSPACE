import { createTheme } from "@mui/material";
const font = "Red Hat Display, Rubik";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#231454",
      light: "#a7a1bb",
      dark: "#0e0822",
      contrastText: "#f4f3f6",
    },
    secondary: {
      main: "#1bc47d",
      light: "#db9fcd",
      dark: "#420634",
      contrastText: "#fbf3f9",
    },
    background: {
      default: "#fff",
      paper: "#F5F5F5",
    },
  },
  typography: {
    fontFamily: font,
  },
  components: {
    MuiInputLabel: {
      styleOverrides: {
        // root: {
        //   transformOrigin: "center",
        // },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderColor: theme.palette.primary.main,
          background: theme.palette.common.white,
          borderRadius: "8px",
          borderWidth: "4px",
        }),
        input: {
          fontSize: "13px",
          padding: "12px",
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        fullWidth: false,
      },
      styleOverrides: {
        root: ({ theme }) => ({
          background: theme.palette.common.white,
          borderRadius: "8px",
          fontSize: "13px",
        }),
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "6px",
          padding: ".5em 2em",
        },
      },
    },
  },
});
