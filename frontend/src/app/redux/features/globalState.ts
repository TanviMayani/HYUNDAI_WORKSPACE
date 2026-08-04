import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface globalState {
  tileState: string | null;
  moduleId: string;
  profileData: {};
  productType: string;
  documentType: string;
  workflowSteps: number;
  workflowId: string;
  docId: string;
  isHistoryDeleted: number;
}

const initialState: globalState = {
  tileState: null,
  moduleId: "",
  profileData: {},
  productType: "",
  documentType: "",
  workflowSteps: 0,
  workflowId: "",
  docId: "",
  isHistoryDeleted: 0,
};

const globalSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setTileState(state, action: PayloadAction<string>) {
      state.tileState = action.payload;
    },
    setModuleId(state, action: PayloadAction<string>) {
      state.moduleId = action.payload;
    },
    setProfileData(state, action: PayloadAction<string>) {
      state.profileData = action.payload;
    },
    setProductType(state, action: PayloadAction<string>) {
      state.productType = action.payload;
    },
    setDocumentType(state, action: PayloadAction<string>) {
      state.documentType = action.payload;
    },
    setWorkflowSteps(state, action: PayloadAction<number>) {
      state.workflowSteps = action.payload;
    },
    setWorkflowId(state, action: PayloadAction<string>) {
      state.workflowId = action.payload;
    },
    setDocId(state, action: PayloadAction<string>) {
      state.docId = action.payload;
    },
    setIsHistoryDeleted(state, action: PayloadAction<number>) {
      state.isHistoryDeleted = action.payload;
    },
  },
});

export const {
  setTileState,
  setDocId,
  setModuleId,
  setProfileData,
  setProductType,
  setDocumentType,
  setWorkflowSteps,
  setWorkflowId,
  setIsHistoryDeleted,
} = globalSlice.actions;

export default globalSlice.reducer;
