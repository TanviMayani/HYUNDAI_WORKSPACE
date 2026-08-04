import CryptoJS from "crypto-js";
// const tokenSecret = import.meta.env.VITE_TOKEN_KEY;

export const tokenEncrypt = (token) => {
  return CryptoJS.AES.encrypt(token, "tokenSecret").toString();
};

export const tokenDecrypt = (token) => {
  return CryptoJS.AES.decrypt(token, "tokenSecret").toString(CryptoJS.enc.Utf8);
};
