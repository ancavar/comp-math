#include <math.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>

#define BLOCK_SIZE 128
#define eps 0.000001

typedef struct net_t {
    double** u;
    double** f;
    double h;
    size_t size;
};

// todo: replace (global variable bad!)
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

double process_block(struct net_t* net, int i, int j) {
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

void process_net(struct net_t* net) {
    int i, j;
    int NB = ceil((double)net->size / BLOCK_SIZE);
    double dmax;
    double dm[NB];
    do {
        counter++;
        dmax = 0.0;
        for (int nx = 0; nx < NB; nx++) {
            dm[nx] = 0;
#pragma omp parallel for shared(nx, dm) private(i,j)
            for (i = 0; i < nx + 1; i++) {
                j = nx - i;
                double d = process_block(net, i, j);
                dm[i] = fmax(dm[i], d);

            }
        }
        for (int nx = NB - 2; nx > -1; nx--) {
#pragma omp parallel for shared(nx, dm) private(i, j)
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

struct net_t init_net(size_t size) {
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

    struct net_t net = {u, f, h, size};
    return net;
}

void free_net(struct net_t* net) {
    for (int i = 0; i < net->size + 1; i++) {
        free(net->u[i]);
        free(net->f[i]);
    }
    free(net->u);
    free(net->f);
}

int main() {

    size_t test_size[6] = {500, 1000, 2000, 3000, 5000, 7000};
    printf("%s%12s%15s%13s\n", "Net size", "Threads", "Iterations", "Time (s)");
    for (int i = 0; i < 6; i++ ) {
        for (int num_threads = omp_get_num_procs(); num_threads > 0; num_threads /= 2) {
            omp_set_num_threads(num_threads);
            double avg_time = 0;
            // todo: a mess with memory leaks , refactor
            int j;
            for (j = 0; j < 5; j++) {
                counter = 0;
                struct net_t net = init_net(test_size[i]);
                double start_time = omp_get_wtime();
                process_net(&net);
//                int p = 3 * net.size / 4;
//            printf("start: %f    end: %f    real: %f\n", fun_u(p * net.h, p * net.h), net.u[p][p],
//                   exp(-(p * net.h * p * net.h)));
                double end_time = omp_get_wtime(); // End timing
                avg_time += end_time - start_time;
                free_net(&net);
            }
            avg_time /= j;
            printf("%ld%12d%11d%22f\n", test_size[i], num_threads, counter, avg_time);
        }
        printf("------------------------------------------------\n");
    }


    return 0;
}
