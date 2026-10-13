#ifndef HOST_CPCT_STUB_H
#define HOST_CPCT_STUB_H
#include <stdint.h>
#include <string.h>
#include <assert.h>
typedef uint8_t u8; typedef uint16_t u16; typedef int16_t i16;
static u8 host_ram[65536];
#define CPCT_VMEM_START ((u8*)0xc000)
#define Key_M 1
#define Key_D 2
static u8* host_ptr(const void* p) {return (uintptr_t)p<65536?host_ram+(uintptr_t)p:(u8*)p;}
static u8* cpct_getScreenPtr(u8* base,u8 x,u8 y) {assert(x<80&&y<200);return host_ptr(base)+(y&7)*2048+(y>>3)*80+x;}
static void cpct_memcpy(void* d,const void* s,u16 n){memcpy(host_ptr(d),host_ptr(s),n);}
static void cpct_drawSolidBox(u8* d,u8 c,u8 w,u8 h){assert(w>=1&&w<=64&&h>=1);memset(d,c,w);}
static u8 cpct_px2byteM0(u8 a,u8 b){return a^b;}
static void cpct_drawSpriteMasked(void* s,u8* d,u8 w,u8 h){(void)s;(void)d;(void)w;(void)h;}
static void cpct_setPalette(u8* p,u8 n){(void)p;(void)n;}
static u8 host_key_d;
static u8 cpct_isKeyPressed(i16 k){return k==Key_D && host_key_d;}
#endif
