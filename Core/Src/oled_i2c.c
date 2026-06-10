#include "oled_i2c.h"
#include "main.h"

extern I2C_HandleTypeDef hi2c1;

#define OLED_WIDTH 128U
#define OLED_HEIGHT 64U
#define OLED_PAGE_COUNT (OLED_HEIGHT / 8U)
#define OLED_FRAME_SIZE (OLED_WIDTH * OLED_PAGE_COUNT)
#define OLED_I2C_TIMEOUT 100U
#define OLED_DATA_CHUNK_SIZE 64U

static void OLED_WriteCommand(uint8_t command)
{
  uint8_t data[2] = {0x00U, command};
  (void)HAL_I2C_Master_Transmit(&hi2c1, OLED_ADDR, data, sizeof(data), OLED_I2C_TIMEOUT);
}

static void OLED_SetFullWindow(void)
{
  OLED_WriteCommand(0x21U);
  OLED_WriteCommand(0x00U);
  OLED_WriteCommand(0x7FU);
  OLED_WriteCommand(0x22U);
  OLED_WriteCommand(0x00U);
  OLED_WriteCommand(0x07U);
}

static void OLED_WriteData(const uint8_t *data, uint16_t size)
{
  uint8_t tx_buffer[OLED_DATA_CHUNK_SIZE + 1U];

  while (size > 0U)
  {
    uint16_t chunk_size = size;
    if (chunk_size > OLED_DATA_CHUNK_SIZE)
    {
      chunk_size = OLED_DATA_CHUNK_SIZE;
    }

    tx_buffer[0] = 0x40U;
    for (uint16_t i = 0U; i < chunk_size; i++)
    {
      tx_buffer[i + 1U] = data[i];
    }

    (void)HAL_I2C_Master_Transmit(&hi2c1, OLED_ADDR, tx_buffer, chunk_size + 1U, OLED_I2C_TIMEOUT);

    data += chunk_size;
    size -= chunk_size;
  }
}

void OLED_Init(void)
{
  HAL_Delay(100U);

  OLED_WriteCommand(0xAEU);
  OLED_WriteCommand(0xD5U);
  OLED_WriteCommand(0x80U);
  OLED_WriteCommand(0xA8U);
  OLED_WriteCommand(0x3FU);
  OLED_WriteCommand(0xD3U);
  OLED_WriteCommand(0x00U);
  OLED_WriteCommand(0x40U);
  OLED_WriteCommand(0x8DU);
  OLED_WriteCommand(0x14U);
  OLED_WriteCommand(0x20U);
  OLED_WriteCommand(0x00U);
  OLED_WriteCommand(0xA1U);
  OLED_WriteCommand(0xC8U);
  OLED_WriteCommand(0xDAU);
  OLED_WriteCommand(0x12U);
  OLED_WriteCommand(0x81U);
  OLED_WriteCommand(0xCFU);
  OLED_WriteCommand(0xD9U);
  OLED_WriteCommand(0xF1U);
  OLED_WriteCommand(0xDBU);
  OLED_WriteCommand(0x40U);
  OLED_WriteCommand(0xA4U);
  OLED_WriteCommand(0xA6U);
  OLED_WriteCommand(0xAFU);

  OLED_Clear();
}

void OLED_Clear(void)
{
  uint8_t zeros[OLED_DATA_CHUNK_SIZE] = {0U};

  OLED_SetFullWindow();
  for (uint16_t offset = 0U; offset < OLED_FRAME_SIZE; offset += OLED_DATA_CHUNK_SIZE)
  {
    OLED_WriteData(zeros, OLED_DATA_CHUNK_SIZE);
  }
}

void OLED_ShowFrame(const uint8_t *frame)
{
  if (frame == 0)
  {
    return;
  }

  OLED_SetFullWindow();
  OLED_WriteData(frame, OLED_FRAME_SIZE);
}
