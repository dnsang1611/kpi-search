import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    selectedImages: []
};

const imageSearchSlice = createSlice({
    name: 'imageSearch',
    initialState,
    reducers: {
        addSelectedImage(state, action) {
            const imageUrl = action.payload;
            // Prevent adding duplicate images
            if (!state.selectedImages.includes(imageUrl)) {
                state.selectedImages.push(imageUrl);
            }
        },
        removeSelectedImage(state, action) {
            const imageUrl = action.payload;
            state.selectedImages = state.selectedImages.filter(img => img !== imageUrl);
        },
        resetSelectedImages(state) {
            state.selectedImages = [];
        }
    }
});

export const { addSelectedImage, removeSelectedImage, resetSelectedImages } = imageSearchSlice.actions;
export default imageSearchSlice.reducer;
