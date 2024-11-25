SAVE_DIR=/mnt/mmlab2024nas/visedit/AIC2024/data/Batch3

(
    wget -P ${SAVE_DIR}	https://atm249499-s3user.vcos.cloudstorage.com.vn/aic24-b9/Videos_L25_a.zip
    unzip ${SAVE_DIR}/Videos_L25_a.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249500-s3user.vcos.cloudstorage.com.vn/aic24-b0/Videos_L26_a.zip
    unzip ${SAVE_DIR}/Videos_L26_a.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249500-s3user.vcos.cloudstorage.com.vn/aic24-b0/Videos_L26_b.zip
    unzip ${SAVE_DIR}/Videos_L26_b.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR} https://atm249500-s3user.vcos.cloudstorage.com.vn/aic24-b0/Videos_L26_c.zip
    unzip ${SAVE_DIR}/Videos_L26_c.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249500-s3user.vcos.cloudstorage.com.vn/aic24-b0/Videos_L26_d.zip
    unzip ${SAVE_DIR}/Videos_L26_d.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249500-s3user.vcos.cloudstorage.com.vn/aic24-b0/Videos_L26_e.zip
    unzip ${SAVE_DIR}/Videos_L26_e.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249499-s3user.vcos.cloudstorage.com.vn/aic24-b9/Videos_L27_a.zip
    unzip ${SAVE_DIR}/Videos_L27_a.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249499-s3user.vcos.cloudstorage.com.vn/aic24-b9/Videos_L28_a.zip
    unzip ${SAVE_DIR}/Videos_L28_a.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249499-s3user.vcos.cloudstorage.com.vn/aic24-b9/Videos_L29_a.zip
    unzip ${SAVE_DIR}/Videos_L29_a.zip -d ${SAVE_DIR}
) &
(
    wget -P ${SAVE_DIR}	https://atm249499-s3user.vcos.cloudstorage.com.vn/aic24-b9/Videos_L30_a.zip
    unzip ${SAVE_DIR}/Videos_L30_a.zip -d ${SAVE_DIR}	
)