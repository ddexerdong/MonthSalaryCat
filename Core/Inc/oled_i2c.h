#ifndef __OLED_I2C_H
#define __OLED_I2C_H

#include <stdint.h>

#define OLED_ADDR (0x3C << 1)

void OLED_Init(void);
void OLED_Clear(void);
void OLED_ShowFrame(const uint8_t *frame);

#endif /* __OLED_I2C_H */
