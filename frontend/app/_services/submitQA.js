import { FETCH } from "./api-server";

export const submitServices = {
    submit_qa: async (id, submitData) => {
        const data = await FETCH.post('public', `submit/${id.evaluationId}?session=${id.sessionId}`, {
            "answerSets": [
                {
                    "answers": [
                        {
                            "text": `${submitData.answer}-${submitData.frame}`
                        }
                    ]
                }
            ]
        })
        return data;
    },
    submit_qa: async (id, submitData) => {
        const data = await FETCH.post('public', `submit/${id.evaluationId}?session=${id.sessionId}`, {
            "answerSets": [
                {
                    "answers": [
                        {
                            "mediaItemName": submitData.frame,
                            "start": submitData.ms,
                            "end": submitData.ms
                        }
                    ]
                }
            ]
        })
        return data;
    },
}
