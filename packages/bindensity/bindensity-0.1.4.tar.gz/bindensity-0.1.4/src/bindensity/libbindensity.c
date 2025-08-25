// Copyright 2020-2024 Jean-Baptiste Delisle
// Licensed under the EUPL-1.2 or later

#include "libbindensity.h"

void resampling_check_def(
  int64_t new_n_in,
  int64_t *isdef,
  int64_t *istart, int64_t *iend)
{
  // Avoid to compute undefined bins

  int64_t i, k;

  for (k=0; k<new_n_in; k++) {
    for (i=istart[k]; i<iend[k]; i++) {
      if (!isdef[i]) {
        iend[k] = istart[k];
        break;
      }
    }
  }
}

void resampling_linear_weights(
  // Shapes
  int64_t new_n_in,
  // Input
  double *dx, double *new_dx_in,
  double *delta,
  int64_t *istart, int64_t *isize,
  // Output
  double *w)
{
  // Compute weights according to linear interpolation rules

  int64_t i, k;
  double *wk;

  wk = w;
  for (k=0; k<new_n_in; k++) {
    if (isize[k] == 0)
      continue;
    // Init
    for (i=0; i<isize[k]; i++) {
      wk[i] = dx[istart[k]+i];
    }
    // Right edge
    wk[isize[k]-1] = delta[k+1];
    // Left edge
    wk[0] -= delta[k];
    for (i=0; i<isize[k]; i++) {
      wk[i] /= new_dx_in[k];
    }
    wk += isize[k];
  }
}

void resampling_cubic_weights(
  // Shapes
  int64_t new_n_in,
  // Input
  int64_t *dl, int64_t *dr,
  double *dx, double *new_dx_in,
  double *Fkleft, double *Fkcenter, double *Fkright,
  int64_t *istart, int64_t *isize,
  // Output
  double *w)
{
  // Compute weights according to cubic interpolation rules

  int64_t i, k;
  double *wk;

  wk = w;
  for (k=0; k<new_n_in; k++) {
    if (isize[k] == 0)
      continue;
    // Init
    for (i=0; i<isize[k]; i++) {
      wk[i] = dx[istart[k]+i];
    }
    if (dl[k]) wk[0] = 0.0;
    if (dr[k+1]) wk[isize[k]-2] = 0.0;
    // Right edge
    wk[isize[k]-1] = Fkright[k+1];
    wk[isize[k]-1-dr[k+1]] += Fkcenter[k+1];
    wk[isize[k]-1-dl[k+1]-dr[k+1]] += Fkleft[k+1];
    // Left edge
    wk[dl[k]+dr[k]] -= Fkright[k];
    wk[dl[k]] -= Fkcenter[k];
    wk[0] -= Fkleft[k];
    for (i=0; i<isize[k]; i++) {
      wk[i] /= new_dx_in[k];
    }
    wk += isize[k];
  }
}

void resampling_y(
  int64_t new_n_in, int64_t kstart,
  int64_t *istart, int64_t *iend, int64_t *isize,
  double *y, double *w,
  double *new_y)
{
  // Compute new bins density

  int64_t i, k;
  double *wk;

  wk = w;
  for (k=0; k<new_n_in; k++) {
    if (isize[k] == 0)
      continue;
    new_y[kstart+k] = 0.0;
    for (i=istart[k]; i<iend[k]; i++) {
      new_y[kstart+k] += wk[i-istart[k]]*y[i];
    }
    wk += isize[k];
  }
}

void resampling_covariance_nd(
  // Shapes
  int64_t nd, int64_t new_n_in,
  // Input
  int64_t *istart, int64_t *iend,
  // Output
  int64_t *new_nd)
{
  // Compute new covariance shape

  int64_t k, l;

  new_nd[0] = 1;
  l = 0;
  k = 2;
  while (k < new_n_in) {
    while ((k < new_n_in) && (istart[k] < iend[l] + nd)) {
      k ++;
      new_nd[0] ++;
    }
    l ++;
    k ++;
  }
}

void resampling_covariance(
  // Shapes
  int64_t n, int64_t nd, int64_t new_n,
  int64_t kstart, int64_t new_n_in,
  // Input
  double *cov,
  int64_t *istart, int64_t *iend, int64_t *isize,
  double *w,
  // Output
  double *new_cov)
{
  // Compute new covariance

  int64_t i, j, d, k, l, b;
  int64_t l0;
  double *wk, *wl;

  wl = w;
  for (l=0; l<new_n_in; l++)
  {
    l0 = kstart + l;
    k = l;
    wk = wl;
    b = 0;
    while ((k < new_n_in) && (istart[k] < iend[l] + nd))
    {
      for (d=-nd; d<=nd; d++)
      {
        for (j=MAX(istart[l], istart[k]-d); j<MIN(iend[l], iend[k]-d); j++)
        {
          i = j + d;
          new_cov[new_n*b+l0] += (wk[i-istart[k]] * wl[j-istart[l]]
            * cov[n*ABS(d)+MIN(i,j)]);
        }
      }
      wk += isize[k];
      k ++;
      b ++;
    }
    wl += isize[l];
  }
}
