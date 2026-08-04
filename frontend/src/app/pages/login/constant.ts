import * as yup from "yup";
export const formikSchema = yup.object().shape({
  email: yup
    .string()
    .email("Please write a valid email")
    .nullable()
    .required("Required"),

  password: yup.string().nullable().required("Required"),
});
