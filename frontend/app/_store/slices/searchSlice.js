import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    result: [],
    activeButtons: ["text"],
    topK: 80,
    query: '',
    objectData: [],
    colorData: Array(25).fill(null),
    sketchData: '',
    poseData: 80,
    temporalData: ["", ""],
    loading: false,
    error: null,
};

const searchSlice = createSlice({
    name: 'search',
    initialState,
    reducers: {
        toggleActiveButton(state, action) {
            const buttonType = action.payload;
            if (state.activeButtons.includes(buttonType)) {
              // Remove the buttonType
              state.activeButtons = state.activeButtons.filter(btn => btn !== buttonType);
            } else {
              // Add the buttonType
              state.activeButtons = [...state.activeButtons, buttonType];
              state.activeButtons = [...new Set(state.activeButtons)];
            }
          },
        resetActiveButtons(state) {
            state.activeButtons = ["text"];
        },
        setActiveButtons(state, action) {
            state.activeButtons = action.payload;
        },
        setTopK(state, action) {
            state.topK = action.payload;
        },
        setResult(state, action) {
            state.result = [];
            state.result = action.payload;
        },
        setQuery(state, action) {
            state.query = action.payload
        },
        setObjectData(state, action) {
            state.objectData = action.payload;
        },
        setColorData(state, action) {
            state.colorData = action.payload;
        },
        resetColorData(state) {
            state.colorData = Array(25).fill(null);
            state.colorHistory = [];
            state.redoHistory = [];
            state.selectedColor = 'black';
          },
        setTemporalData(state, action) {
            state.temporalData = action.payload;
        },
        setPoseData(state, action) {
            state.poseData = action.payload;
        },
        setSketchData(state, action) {
            state.sketchData = action.payload;
        },
        clearResult(state) {
            state.result = [];
        },
        resetData(state) {
            state.objectData = [];
            state.colorData = [];
            state.sketchData = '';
            state.poseData = 80;
            state.temporalData = ["", ""];
            state.result = [];
            state.query = '';
            state.activeButtons = ["text"];
            state.topK = 80;
            state.loading = false;
            state.error = null;
        }
    },
});

export const { 
    toggleActiveButton, 
    resetActiveButtons, 
    setTopK, 
    setResult, 
    setQuery, 
    setObjectData, 
    setColorData, 
    resetColorData,
    setTemporalData, 
    setPoseData, 
    setSketchData,
    resetData,
} = searchSlice.actions;

export default searchSlice.reducer;
