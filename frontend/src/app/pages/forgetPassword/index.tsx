import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  Divider,
  InputAdornment,
} from "@mui/material";
import { useEffect, useState } from "react";
import * as yup from "yup";
import { useFormik } from "formik";
import { AlternateEmail } from "@mui/icons-material";
import { useNavigate, Link } from "react-router-dom";
import { useForgotPasswordMutation } from "../../redux/features/commonApis";
import toast from "react-hot-toast";

const formikSchema = yup.object().shape({
  email: yup
    .string()
    .email("Please write a valid email")
    .nullable()
    .required("Email is Required"),
});

const ForgotPasswordForm = () => {
  const navigate = useNavigate()

  const [forgotPassword, {isSuccess, isLoading}] = useForgotPasswordMutation()

  const [success, setSuccess] = useState<boolean>(false)
  const formik = useFormik({
    initialValues: {
      email: "",
    },
    validationSchema: formikSchema,
    onSubmit: (values) => {
        forgotPassword(values)
    },
  });

  useEffect(() => {
    isLoading && toast.loading("Loading...")
  },[isLoading])

  useEffect(() => {
    isSuccess && setSuccess(true)
  }, [isSuccess])

  return (
    <Box
      sx={{
        width: "80%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box
        sx={{
          p: 3,
          borderRadius: "8px",
          display: "flex",
          flexDirection: "column",
          boxShadow: `0px 3px 12px 0px rgba(0, 0, 0, 0.19)`,
        }}
      >
        <Typography component="h1" variant="h5" fontWeight={"bold"}>
          Forgot Password
        </Typography>
        <Typography component="h2" variant="subtitle2" color={"secondary"}>
          {`Enter your email  and we'll send you a verification link to reset your password.`}
        </Typography>
        <Divider sx={{ my: 1, pt: 2 }} />
        <Box
          component="form"
          onSubmit={formik.handleSubmit}
          noValidate
          sx={{ mt: 1 }}
        >
          {
            success ?  <Typography component="h6" variant="h6" fontWeight={"bold"}>
            Verification link sent successfully to your email.
          </Typography> : <>
            <TextField
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <AlternateEmail />
              </InputAdornment>
            ),
          }}
            margin="normal"
            required
            fullWidth
            id="email"
            size="small"
            placeholder="Email*"
            name="email"
            autoComplete="email"
            autoFocus
            error={!!(formik.touched.email && formik.errors.email)}
            onChange={formik.handleChange}
            value={formik.values.email}
            helperText={
              formik.touched.email && formik.errors.email
            }
          />
          <Box display="flex" alignItems="center" gap={2}>
          <Button
            fullWidth
            type="submit"
            variant="contained"
            disabled={isLoading}
            sx={{ my: 3, py: 1 }}
          >
            {`Submit`}
          </Button>
          <Button
            fullWidth
            type="button"
            variant="outlined"
            onClick={() => navigate("/login")}
            sx={{ my: 3, py: 1 }}
          >
            {`Cancel`}
          </Button>
          </Box>
          <Grid container>
            <Grid item xs>
              <Typography
                component={"span"}
                variant="body2"
              >{`Already have an account? `}</Typography>
              <Link to="/login" className="link">
                {`Sign In`}
              </Link>
            </Grid>
            <Grid item>
              <Typography
                component={"span"}
                variant="body2"
              >{`Don't have an account? `}</Typography>
              <Link to="/register" className="link">
                {"Sign Up"}
              </Link>
            </Grid>
          </Grid>
            </>
          }
        </Box>
      </Box>
    </Box>
  );
};

export default ForgotPasswordForm;
