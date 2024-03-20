#include <math.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>


int BLOCK_SIZE = 32;

#define eps 0.000001

// number of samples
#define SAMPLE_SIZE 10

typedef struct {
    double **u;
    double **f;
    double h;
    size_t size;
} net_t;

typedef struct {
    double avg_time;
    double std_dev;
} stats_t;



int counter;

// todo: hardcoded -- bad!!!
double fun_f(double x, double y) {
    return exp(x * y) * (x * x + y * y);
}
double fun_u(double x, double y) {
    if (x == 0 || y == 0) {
        return 1.0;
    }
    if (x == 1) {
        return exp(-y);
    }
    if (y == 1) {
        return exp(-x);
    }
    // Taylor's series for e^(-xy) (initial approximation)
    return 1 - (x*y) + (1.0/2)*pow(x*y, 2.0); // + (1.0/24) * pow(x*y, 4.0) ;

}

double book_fun_f(double x, double y) {
    return 0;
}
double book_fun_u(double x, double y) {
    if (x == 0) {
        return 100-200*y;
    }
    if (y == 0) {
        return 100-200*x;
    }
    if (x == 1) {
        return -100+200*y;
    }
    if (y == 1) {
        return -100+200*x;
    }

    srand(9255132);
    // random approximation [-100; 100]
    return (rand() % 201) - 100;


}

double process_block(net_t* net, int i, int j) {
    double dmax = 0;
    int i_start = 1 + i * BLOCK_SIZE;
    int j_start = 1 + j * BLOCK_SIZE;
    int i_end = fmin(i_start + BLOCK_SIZE, net->size);
    int j_end = fmin(j_start + BLOCK_SIZE, net->size);
    for (int i = i_start; i <= i_end; i++) {
        for (int j = j_start; j <= j_end; j++) {
            double temp = net->u[i][j];
            net->u[i][j] = 0.25 * (net->u[i - 1][j] + net->u[i + 1][j] + net->u[i][j - 1] + net->u[i][j + 1] -
                                   net->h * net->h * net->f[i][j]);
            dmax = fmax(dmax, fabs(temp - net->u[i][j]));
        }
    }
    return dmax;
}

void process_net(net_t* net) {
    int i, j, nx;
    int NB = ceil((double)net->size / BLOCK_SIZE);
    double dmax;
    double dm[NB];
    do {
        counter++;
        dmax = 0.0;
        for (nx = 0; nx < NB; nx++) {
            dm[nx] = 0;
#pragma omp parallel for shared(dmax, nx, dm) private(i,j)
            for (i = 0; i < nx + 1; i++) {
                j = nx - i;
                double d = process_block(net, i, j);
                dm[i] = fmax(dm[i], d);

            }
        }
        for (int nx = NB - 2; nx > -1; nx--) {
#pragma omp parallel for shared(dmax, nx, dm) private(i,j)
            for (i = 0; i < nx + 1; i++) {
                j = 2 * (NB - 1) - nx - i;
                double d = process_block(net, i, j);
                dm[i] = fmax(dm[i], d);
            }
        }
        for (i = 0; i < NB; i++) {
            dmax = fmax(dmax, dm[i]);
        }

    } while (dmax > eps);
}

double** allocate_array(size_t size) {
    double **x;
    x = malloc(size * sizeof *x);
    for (int i=0; i<size; i++) {
        x[i] = malloc(size * sizeof *x[i]);
    }
    return x;
}

net_t init_net(size_t size) {
    // size (according to the book) refers to an inner matrix
    // that is without borders, hence size + 1
    double** u = allocate_array(size+2);
    double** f = allocate_array(size+2);
    double h = 1.0 / size;
    for (int i = 0; i < size+2; i++) {
        for (int j = 0; j < size+2; j++) {
            u[i][j] = fun_u(i * h, j * h); // initial guess for solution
            f[i][j] = fun_f(i * h, j * h);
        }
    }

    net_t net = {u, f, h, size};
    return net;
}

void free_net(net_t* net) {
    for (int i = 0; i < net->size + 1; i++) {
        free(net->u[i]);
        free(net->f[i]);
    }
    free(net->u);
    free(net->f);
}


void calculate_stats(double *times, int n, stats_t *stats) {
    double sum = 0;
    for (int i = 0; i < n; i++) {
        sum += times[i];
    }
    stats->avg_time = sum / n;

    double sum_of_squares = 0;
    for (int i = 0; i < n; i++) {
        sum_of_squares += pow(times[i] - stats->avg_time, 2);
    }
    stats->std_dev = sqrt(sum_of_squares / (n - 1));
}

int main() {

    size_t bench[48];
    for (int i = 0; i <= 40; i++) {
        bench[i] = ceil(500 + 30*pow(i, 1.3));
    }

    int num_threads_list[6] = {1, 2, 4, 8};

    size_t test_block_size[9] = {16, 32, 48, 64, 86, 108, 128, 192, 256};
    size_t test_size[6] = {500, 1000, 2000, 3000, 5000, 7000};
    printf("| %s | %s | %s | %s | %s | %s |\n", "Net size", "Block size", "Threads", "Iterations", "Mean time (s)", "Standard dev.");
    printf("|----------|------------|---------|------------|---------------|---------------|\n");

    double times[SAMPLE_SIZE];
    for (int blck_sz = 0; blck_sz <= 8; blck_sz++) {
        BLOCK_SIZE = test_block_size[blck_sz];
        for (int i = 0; i <= 5; i++ ) {
            for (int k = 16; k >= 1; k /= 2 ) {
                omp_set_num_threads(k);
                for (int j = 0; j < SAMPLE_SIZE; j++) {
                    counter = 0;
                    net_t net = init_net(test_size[i]);
                    double start_time = omp_get_wtime();
                    process_net(&net);
    //                int p = 3 * net.size / 4;
    //            printf("start: %f    end: %f    real: %f\n", fun_u(p * net.h, p * net.h), net.u[p][p],
    //                   exp(-(p * net.h * p * net.h)));
                    double end_time = omp_get_wtime(); // End timing
                    times[j] = end_time - start_time;
                    free_net(&net);
                }

                stats_t stats;
                calculate_stats(times, SAMPLE_SIZE, &stats);
                printf("| %8ld | %10d | %7d | %10d | %13f | %13f |\n", test_size[i], BLOCK_SIZE, k, counter, stats.avg_time, stats.std_dev);
            }
        }
    }

    return 0;
}
