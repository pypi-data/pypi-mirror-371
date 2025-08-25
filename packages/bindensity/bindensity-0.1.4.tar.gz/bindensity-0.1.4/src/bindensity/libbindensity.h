// Copyright 2020-2024 Jean-Baptiste Delisle
// Licensed under the EUPL-1.2 or later

#include <stdint.h>
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define ABS(a) (((a) > 0) ? (a) : -(a))

void resampling_check_def(
  int64_t new_n_in,
  int64_t *isdef,
  int64_t *istart, int64_t *iend);

void resampling_linear_weights(
  // Shapes
  int64_t new_n_in,
  // Input
  double *dx, double *new_dx_in,
  double *delta,
  int64_t *istart, int64_t *isize,
  // Output
  double *w);

void resampling_cubic_weights(
  // Shapes
  int64_t new_n_in,
  // Input
  int64_t *dl, int64_t *dr,
  double *dx, double *new_dx_in,
  double *Fkleft, double *Fkcenter, double *Fkright,
  int64_t *istart, int64_t *isize,
  // Output
  double *w);

void resampling_y(
  int64_t new_n_in, int64_t kstart,
  int64_t *istart, int64_t *iend, int64_t *isize,
  double *y, double *w,
  double *new_y);

void resampling_covariance_nd(
  // Shapes
  int64_t nd, int64_t new_n_in,
  // Input
  int64_t *istart, int64_t *iend,
  // Output
  int64_t *new_nd);

void resampling_covariance(
  // Shapes
  int64_t n, int64_t nd, int64_t new_n,
  int64_t kstart, int64_t new_n_in,
  // Input
  double *cov,
  int64_t *istart, int64_t *iend, int64_t *isize,
  double *w,
  // Output
  double *new_cov);
