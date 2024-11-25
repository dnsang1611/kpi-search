import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    relevantImages: [],
    irrelevantImages: [],
};

const rerankSlice = createSlice({
    name: 'rerank',
    initialState,
    reducers: {
        addRelevantImage(state, action) {
            const image = action.payload;
            if (!state.relevantImages.includes(image)) {
                state.relevantImages.push(image);
                state.irrelevantImages = state.irrelevantImages.filter(img => img !== image);
            }
        },
        removeRelevantImage(state, action) {
            const image = action.payload;
            state.relevantImages = state.relevantImages.filter(img => img !== image);
        },
        addIrrelevantImage(state, action) {
            const image = action.payload;
            if (!state.irrelevantImages.includes(image)) {
                state.irrelevantImages.push(image);
                state.relevantImages = state.relevantImages.filter(img => img !== image);
            }
        },
        removeIrrelevantImage(state, action) {
            const image = action.payload;
            state.irrelevantImages = state.irrelevantImages.filter(img => img !== image);
        },
        resetRerank(state) {
            state.relevantImages = [];
            state.irrelevantImages = [];
        },
    },
});

export const {
    addRelevantImage,
    removeRelevantImage,
    addIrrelevantImage,
    removeIrrelevantImage,
    resetRerank,
} = rerankSlice.actions;

export default rerankSlice.reducer;
