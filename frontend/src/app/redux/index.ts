import { configureStore } from "@reduxjs/toolkit";
import storage from "redux-persist/lib/storage";
import { persistReducer } from "redux-persist";
import { combineReducers } from "redux";
import { encryptTransform } from "redux-persist-transform-encrypt";
import authReducer from "./features/auth/authSlice";
import { profileApis } from "./features/profile";
import { jobsApis } from "./features/jobs";
import { membersApis } from "./features/members/index.tsx";
import { groupsApis } from "./features/groups";
import { businessProfileApis } from "./features/business";
import { analyticsApi } from "./features/analytics";
import { docQueryApis } from "./features/doc-query/index.ts";
import { summerizeApi } from "./features/summerize/index.ts";
import { translationApi } from "./features/translation/index.ts";

import globalStateReducer from "./features/globalState.ts";
import { commonApis } from "./features/commonApis.ts";

// const persistKey = import.meta.env.VITE_PERSISTOR_KEY;
export type AppDispatch = typeof store.dispatch;

const reducers = combineReducers({
  globalState: globalStateReducer,
  auth: authReducer,
  [profileApis.reducerPath]: profileApis.reducer,
  [jobsApis.reducerPath]: jobsApis.reducer,
  [businessProfileApis.reducerPath]: businessProfileApis.reducer,
  [membersApis.reducerPath]: membersApis.reducer,
  [groupsApis.reducerPath]: groupsApis.reducer,
  [analyticsApi.reducerPath]: analyticsApi.reducer,
  [docQueryApis.reducerPath]: docQueryApis.reducer,
  [summerizeApi.reducerPath]: summerizeApi.reducer,
  [translationApi.reducerPath]: translationApi.reducer,

  [commonApis.reducerPath]: commonApis.reducer,
});

const rootReducer = (state, action) => {
  if (action.type === "logout/logout") {
    state = undefined;
  }
  return reducers(state, action);
};

const persistConfig = {
  key: "root",
  storage,
  transforms: [
    encryptTransform({
      secretKey: "persistKey",
      onError: function (error) {
        console.warn(error);
      },
    }),
  ],
  whitelist: ["auth", "globalState"], // Only persist 'auth' and 'globalState'
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  devTools: true,
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware: any) =>
    [
      ...getDefaultMiddleware(),
      profileApis.middleware,
      jobsApis.middleware,
      membersApis.middleware,
      groupsApis.middleware,
      analyticsApi.middleware,
      businessProfileApis.middleware,
      commonApis.middleware,
      docQueryApis.middleware,
      summerizeApi.middleware,
      translationApi.middleware,
    ].filter(Boolean) as any,
});
